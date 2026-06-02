package com.example.warsawbeauty.salon;

public record SalonImportRecord(
        Long osmId,
        String osmType,
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
        String openingHours
) {

    Salon toEntity() {
        Salon salon = new Salon();
        salon.setOsmId(osmId);
        salon.setOsmType(osmType);
        salon.setName(name);
        salon.setAddress(address);
        salon.setDistrict(district);
        salon.setPhone(phone);
        salon.setWebsite(website);
        salon.setServices(services);
        salon.setPriceRange(priceRange);
        salon.setRating(rating);
        salon.setReviewsCount(reviewsCount);
        salon.setLatitude(latitude);
        salon.setLongitude(longitude);
        salon.setSource(source);
        salon.setSourceUrl(sourceUrl);
        salon.setOpeningHours(openingHours);
        return salon;
    }
}
