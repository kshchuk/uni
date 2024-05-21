package org.example.dto;

import lombok.Data;

import java.util.List;

@Data
public class TeamDTO {
    private String teamId;
    private String dispatcherId;
    private List<String> specialistIds;
    private List<String> workPlanIds;
}
