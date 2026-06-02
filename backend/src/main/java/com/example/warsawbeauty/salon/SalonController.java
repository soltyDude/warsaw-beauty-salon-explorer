package com.example.warsawbeauty.salon;

import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class SalonController {

    private final SalonService salonService;

    public SalonController(SalonService salonService) {
        this.salonService = salonService;
    }

    @GetMapping("/salons")
    public List<SalonListDto> getSalons(@RequestParam(required = false) String district) {
        return salonService.getSalons(district);
    }

    @GetMapping("/salons/{id}")
    public SalonDetailDto getSalon(@PathVariable long id) {
        return salonService.getSalon(id);
    }

    @PatchMapping("/salons/{id}")
    public SalonDetailDto updateSalon(@PathVariable long id, @Valid @RequestBody SalonUpdateRequest request) {
        return salonService.updateSalon(id, request);
    }

    @GetMapping("/districts")
    public List<String> getDistricts() {
        return salonService.getDistricts();
    }

    @GetMapping("/stats")
    public SalonStatsDto getStats() {
        return salonService.getStats();
    }
}
