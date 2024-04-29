package org.example.dto;

import lombok.Data;

@Data
public class RequestDTO {
    private String requestId;
    private String tenantId;
    private String workType;
    private String scopeOfWork;
    private String desiredTime;
}
