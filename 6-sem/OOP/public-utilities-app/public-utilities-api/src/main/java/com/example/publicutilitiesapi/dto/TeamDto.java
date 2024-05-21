package com.example.publicutilitiesapi.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Value;

import java.io.Serializable;
import java.util.UUID;

/**
 * DTO for {@link com.example.publicutilitiesapi.entity.Team}
 */
@Value
public class TeamDto implements Serializable {
    UUID id;
    @NotNull
    SpecialistDto dispatcher;
}