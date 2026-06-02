package com.example.warsawbeauty.salon;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;

public record SalonUpdateRequest(
        @Pattern(regexp = ".*\\S.*", message = "name must not be blank")
        @Size(max = 255, message = "name is too long")
        String name,

        @Size(max = 500, message = "address is too long")
        String address,

        @Size(max = 100, message = "district is too long")
        String district,

        @Pattern(regexp = "^$|[+0-9() .-]{5,40}$", message = "phone format is invalid")
        String phone,

        @Pattern(regexp = "^$|https?://.+\\..+$", message = "website must be an http(s) URL")
        @Size(max = 500, message = "website is too long")
        String website,

        @Size(max = 1000, message = "services is too long")
        String services,

        @Size(max = 30, message = "priceRange is too long")
        String priceRange,

        @DecimalMin(value = "0.0", message = "rating must be at least 0")
        @DecimalMax(value = "5.0", message = "rating must be at most 5")
        Double rating,

        @PositiveOrZero(message = "reviewsCount cannot be negative")
        Integer reviewsCount
) {
}
