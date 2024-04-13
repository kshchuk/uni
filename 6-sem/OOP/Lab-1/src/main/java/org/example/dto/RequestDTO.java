package org.example.dto;

import lombok.Data;

import java.time.Duration;
import java.util.UUID;

@Data
public class RequestDTO {
    private UUID requestId;
    private UUID tenantId;
    private String workType;
    private String scopeOfWork;
    private Duration desiredTime;
}
