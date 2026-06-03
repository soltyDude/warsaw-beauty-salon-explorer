package com.example.warsawbeauty.salon;

public record SalonListDto(
        Long id,
        String name,
        String district,
        Double rating,
        String priceRange,
        String services,
        String phone,
        String website,
        Integer reviewsCount,
        String openingHours,
        Double latitude,
        Double longitude
) {
}