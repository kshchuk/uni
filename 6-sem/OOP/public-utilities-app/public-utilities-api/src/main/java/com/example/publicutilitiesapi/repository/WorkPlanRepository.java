package com.example.publicutilitiesapi.repository;

import com.example.publicutilitiesapi.entity.WorkPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface WorkPlanRepository extends JpaRepository<WorkPlan, UUID> {

    @Query("SELECT wp.id, wp.description, wp.duration, wp.team.id " +
            "FROM WorkPlan wp " +
            "INNER JOIN wp.team t " +
            "WHERE t.dispatcher.id = ?1")
    List<WorkPlan> findAllByDispatcherId(UUID dispatcherId);

    List<WorkPlan> findAllByTeamId(UUID teamId);
    Long countWorkPlansByTeamId(UUID teamId);
}
