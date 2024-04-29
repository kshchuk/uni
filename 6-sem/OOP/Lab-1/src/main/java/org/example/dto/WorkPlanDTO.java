package org.example.dto;

import lombok.Data;

import java.time.Duration;
import java.util.UUID;

@Data
public class WorkPlanDTO {
    private String workPlanId;
    private String description;
    private String duration;
    private String teamId;
}
