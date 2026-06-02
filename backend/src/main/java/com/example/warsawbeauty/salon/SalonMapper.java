package com.example.warsawbeauty.salon;

final class SalonMapper {

    private SalonMapper() {
    }

    static SalonListDto toListDto(Salon salon) {
        return new SalonListDto(
                salon.getId(),
                salon.getName(),
                salon.getDistrict(),
                salon.getRating(),
                salon.getPriceRange(),
                salon.getServices(),
                salon.getLatitude(),
                salon.getLongitude()
        );
    }

    static SalonDetailDto toDetailDto(Salon salon) {
        return new SalonDetailDto(
                salon.getId(),
                salon.getName(),
                salon.getAddress(),
                salon.getDistrict(),
                salon.getPhone(),
                salon.getWebsite(),
                salon.getServices(),
                salon.getPriceRange(),
                salon.getRating(),
                salon.getReviewsCount(),
                salon.getLatitude(),
                salon.getLongitude(),
                salon.getSource(),
                salon.getSourceUrl(),
                salon.getOsmType(),
                salon.getOsmId(),
                salon.getOpeningHours()
        );
    }
}
