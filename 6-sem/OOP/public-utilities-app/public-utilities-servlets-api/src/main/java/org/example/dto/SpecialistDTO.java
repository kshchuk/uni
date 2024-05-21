package org.example.dto;

import lombok.Data;

import java.util.List;

@Data
public class SpecialistDTO {
    private String specialistId;
    private String name;
    private String specialization;
    private String teamId;
    private List<String> workPlanIds;
}
