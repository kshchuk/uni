package com.example.publicutilitiesapi.repository;

import com.example.publicutilitiesapi.entity.WorkPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface WorkPlanRepository extends JpaRepository<WorkPlan, UUID> {
}