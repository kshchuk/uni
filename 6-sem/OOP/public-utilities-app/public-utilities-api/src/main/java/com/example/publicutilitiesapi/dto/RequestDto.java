package com.example.publicutilitiesapi.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Value;

import java.io.Serializable;
import java.util.UUID;

/**
 * DTO for {@link com.example.publicutilitiesapi.entity.Request}
 */
@Value
public class RequestDto implements Serializable {
    UUID id;
    @NotNull
    TenantDto tenant;
    @NotNull
    @Size(max = 255)
    String workType;
    @NotNull
    @Size(max = 255)
    String scopeOfWork;
    Object desiredTime;
}