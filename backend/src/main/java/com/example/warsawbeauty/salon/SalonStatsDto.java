package com.example.warsawbeauty.salon;

public record SalonStatsDto(
        long totalSalons,
        long districts,
        long withPhone,
        long withWebsite,
        long withServices
) {
}