package com.example.publicutilitiesapi.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Value;

import java.io.Serializable;
import java.util.UUID;

/**
 * DTO for {@link com.example.publicutilitiesapi.entity.Tenant}
 */
@Value
public class TenantDto implements Serializable {
    UUID id;
    @NotNull
    @Size(max = 255)
    String name;
    @NotNull
    @Size(max = 255)
    String address;
}