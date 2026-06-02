package com.example.warsawbeauty.salon;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import org.springframework.core.io.ClassPathResource;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class SalonDataImporter implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(SalonDataImporter.class);

    private final SalonRepository salonRepository;
    private final ObjectMapper objectMapper;
    private final boolean importEnabled;
    private final String importPath;

    public SalonDataImporter(
            SalonRepository salonRepository,
            ObjectMapper objectMapper,
            @Value("${app.data.import.enabled:true}") boolean importEnabled,
            @Value("${app.data.import.path:classpath:data/salons_clean.json}") String importPath    ) {
        this.salonRepository = salonRepository;
        this.objectMapper = objectMapper;
        this.importEnabled = importEnabled;
        this.importPath = importPath;
    }

    @Override
    public void run(String... args) throws IOException {
        if (!importEnabled) {
            logger.info("Salon data import is disabled");
            return;
        }
        if (salonRepository.count() > 0) {
            logger.info("Salon table already contains data; skipping seed import");
            return;
        }

        ClassPathResource resource = new ClassPathResource("data/salons_clean.json");

        if (!resource.exists()) {
            logger.warn("Clean salon dataset was not found at classpath:data/salons_clean.json; backend starts with an empty database");
            return;
        }

        List<SalonImportRecord> records;

        try (InputStream inputStream = resource.getInputStream()) {
            records = objectMapper.readValue(
                    inputStream,
                    new TypeReference<>() {}
            );
        }

        List<Salon> salons = records.stream()
                .filter(record -> StringUtils.hasText(record.name()))
                .map(SalonImportRecord::toEntity)
                .toList();

        salonRepository.saveAll(salons);

        logger.info(
                "Imported {} salons from classpath:data/salons_clean.json",
                salons.size()
        );
    }
}
