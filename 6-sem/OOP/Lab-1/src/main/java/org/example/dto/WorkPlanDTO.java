package org.example.dto;

import lombok.Data;

import java.time.Duration;
import java.util.UUID;

@Data
public class WorkPlanDTO {
    private UUID workPlanId;
    private String description;
    private Duration duration;
    private UUID teamId;
}
