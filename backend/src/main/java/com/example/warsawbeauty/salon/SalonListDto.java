package com.example.warsawbeauty.salon;

public record SalonListDto(
        Long id,
        String name,
        String district,
        Double rating,
        String priceRange,
        String services,
        Double latitude,
        Double longitude
) {
}