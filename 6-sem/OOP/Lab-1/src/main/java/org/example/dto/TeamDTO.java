package org.example.dto;

import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class TeamDTO {
    private String teamId;
    private String dispatcherId;
    private List<String> specialistIds;
    private List<String> workPlanIds;
}
