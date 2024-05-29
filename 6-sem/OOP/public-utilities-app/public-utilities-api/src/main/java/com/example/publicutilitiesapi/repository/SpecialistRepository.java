package com.example.publicutilitiesapi.repository;

import com.example.publicutilitiesapi.entity.Specialist;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface SpecialistRepository extends JpaRepository<Specialist, UUID> {
    List<Specialist> findAllByTeamId(UUID teamId);
    Long countSpecialistsByTeamId(UUID teamId);
}