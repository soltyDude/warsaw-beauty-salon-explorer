package com.example.warsawbeauty.salon;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface SalonRepository extends JpaRepository<Salon, Long> {

    List<Salon> findAllByOrderByNameAsc();

    List<Salon> findByDistrictIgnoreCaseOrderByNameAsc(String district);

    @Query("select distinct s.district from Salon s where s.district is not null and s.district <> ''")
    List<String> findDistinctDistricts();

    @Query("select count(s) from Salon s where s.phone is not null and s.phone <> ''")
    long countWithPhone();

    @Query("select count(s) from Salon s where s.website is not null and s.website <> ''")
    long countWithWebsite();

    @Query("select count(s) from Salon s where s.services is not null and s.services <> ''")
    long countWithServices();
}
