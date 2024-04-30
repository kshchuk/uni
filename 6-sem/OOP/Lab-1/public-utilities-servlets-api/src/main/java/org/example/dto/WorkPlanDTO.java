package org.example.dto;

import lombok.Data;

@Data
public class WorkPlanDTO {
    private String workPlanId;
    private String description;
    private String duration;
    private String teamId;
}
