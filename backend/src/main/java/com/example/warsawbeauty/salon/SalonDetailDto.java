package com.example.warsawbeauty.salon;

public record SalonDetailDto(
        Long id,
        String name,
        String address,
        String district,
        String phone,
        String website,
        String services,
        String priceRange,
        Double rating,
        Integer reviewsCount,
        Double latitude,
        Double longitude,
        String source,
        String sourceUrl,
        String osmType,
        Long osmId,
        String openingHours
) {
}
