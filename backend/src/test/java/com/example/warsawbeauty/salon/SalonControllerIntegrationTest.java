package com.example.warsawbeauty.salon;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class SalonControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private SalonRepository salonRepository;

    private Long salonId;

    @BeforeEach
    void setUp() {
        salonRepository.deleteAll();

        Salon mokotow = new Salon();
        mokotow.setName("Real Hair Warsaw");
        mokotow.setAddress("ul. Pulawska 1, Warsaw");
        mokotow.setDistrict("Mokotow");
        mokotow.setPriceRange("moderate");
        mokotow.setRating(4.4);
        mokotow.setReviewsCount(12);
        mokotow.setLatitude(52.2);
        mokotow.setLongitude(21.0);
        mokotow.setSource("OpenStreetMap");

        Salon wola = new Salon();
        wola.setName("Beauty Studio Wola");
        wola.setAddress("ul. Prosta 2, Warsaw");
        wola.setDistrict("Wola");
        wola.setPriceRange("standard");
        wola.setLatitude(52.23);
        wola.setLongitude(20.98);
        wola.setSource("OpenStreetMap");

        salonRepository.save(wola);
        salonId = salonRepository.save(mokotow).getId();
    }

    @Test
    void listsSalonsAndSupportsDistrictFilter() throws Exception {
        mockMvc.perform(get("/api/salons").param("district", "Mokotow"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].name").value("Real Hair Warsaw"))
                .andExpect(jsonPath("$[0].district").value("Mokotow"))
                .andExpect(jsonPath("$[0].rating").value(4.4))
                .andExpect(jsonPath("$[0].priceRange").value("moderate"));
    }

    @Test
    void returnsSalonDetails() throws Exception {
        mockMvc.perform(get("/api/salons/{id}", salonId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Real Hair Warsaw"))
                .andExpect(jsonPath("$.address").value("ul. Pulawska 1, Warsaw"))
                .andExpect(jsonPath("$.latitude").value(52.2));
    }

    @Test
    void updatesSalon() throws Exception {
        String body = """
                {
                  "phone": "+48 123 456 789",
                  "website": "https://example.com",
                  "rating": 4.8,
                  "reviewsCount": 20
                }
                """;

        mockMvc.perform(patch("/api/salons/{id}", salonId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.phone").value("+48 123 456 789"))
                .andExpect(jsonPath("$.website").value("https://example.com"))
                .andExpect(jsonPath("$.rating").value(4.8))
                .andExpect(jsonPath("$.reviewsCount").value(20));
    }

    @Test
    void returns404ForMissingSalon() throws Exception {
        mockMvc.perform(get("/api/salons/{id}", 999999))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value("NOT_FOUND"));
    }
}
