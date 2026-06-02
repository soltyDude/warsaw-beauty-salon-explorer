package com.example.warsawbeauty.salon;

import java.util.Comparator;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
public class SalonService {

    private final SalonRepository salonRepository;

    public SalonService(SalonRepository salonRepository) {
        this.salonRepository = salonRepository;
    }

    @Transactional(readOnly = true)
    public List<SalonListDto> getSalons(String district) {
        List<Salon> salons = StringUtils.hasText(district)
                ? salonRepository.findByDistrictIgnoreCaseOrderByNameAsc(district.trim())
                : salonRepository.findAllByOrderByNameAsc();
        return salons.stream().map(SalonMapper::toListDto).toList();
    }

    @Transactional(readOnly = true)
    public SalonDetailDto getSalon(long id) {
        return SalonMapper.toDetailDto(findSalon(id));
    }

    @Transactional(readOnly = true)
    public List<String> getDistricts() {
        return salonRepository.findDistinctDistricts().stream()
                .filter(StringUtils::hasText)
                .sorted(Comparator.naturalOrder())
                .toList();
    }

    @Transactional
    public SalonDetailDto updateSalon(long id, SalonUpdateRequest request) {
        Salon salon = findSalon(id);
        if (request.name() != null) {
            salon.setName(request.name().trim());
        }
        if (request.address() != null) {
            salon.setAddress(cleanBlank(request.address()));
        }
        if (request.district() != null) {
            salon.setDistrict(cleanBlank(request.district()));
        }
        if (request.phone() != null) {
            salon.setPhone(cleanBlank(request.phone()));
        }
        if (request.website() != null) {
            salon.setWebsite(cleanBlank(request.website()));
        }
        if (request.services() != null) {
            salon.setServices(cleanBlank(request.services()));
        }
        if (request.priceRange() != null) {
            salon.setPriceRange(cleanBlank(request.priceRange()));
        }
        if (request.rating() != null) {
            salon.setRating(request.rating());
        }
        if (request.reviewsCount() != null) {
            salon.setReviewsCount(request.reviewsCount());
        }
        return SalonMapper.toDetailDto(salonRepository.save(salon));
    }

    @Transactional(readOnly = true)
    public SalonStatsDto getStats() {
        return new SalonStatsDto(
                salonRepository.count(),
                salonRepository.findDistinctDistricts().size(),
                salonRepository.countWithPhone(),
                salonRepository.countWithWebsite(),
                salonRepository.countWithServices()
        );
    }

    private Salon findSalon(long id) {
        return salonRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Salon " + id + " was not found"));
    }

    private String cleanBlank(String value) {
        return StringUtils.hasText(value) ? value.trim() : null;
    }
}
