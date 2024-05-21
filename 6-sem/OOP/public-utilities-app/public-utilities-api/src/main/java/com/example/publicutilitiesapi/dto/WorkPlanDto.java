package com.example.publicutilitiesapi.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Value;

import java.io.Serializable;
import java.util.UUID;

/**
 * DTO for {@link com.example.publicutilitiesapi.entity.WorkPlan}
 */
@Value
public class WorkPlanDto implements Serializable {
    UUID id;
    @NotNull
    @Size(max = 255)
    String description;
    Object duration;
    @NotNull
    TeamDto team;
}