package org.example.dto;

import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class SpecialistDTO {
    private UUID specialistId;
    private String name;
    private String specializtion;
    private UUID teamId;
    private List<UUID> workPlanIds;
}
