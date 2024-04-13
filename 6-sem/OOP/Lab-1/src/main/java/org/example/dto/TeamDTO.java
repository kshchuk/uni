package org.example.dto;

import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class TeamDTO {
    private UUID teamId;
    private UUID dispatcherId;
    private List<UUID> specialistIds;
    private List<UUID> workPlanIds;
}
