package com.example.publicutilitiesapi.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

import java.util.UUID;

@Getter
@Setter
@Entity
@Table(name = "request")
public class Request {
    @Id
    @Column(name = "request_id", nullable = false)
    private UUID id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "tenant_id", nullable = false)
    private Tenant tenant;

    @Size(max = 255)
    @NotNull
    @Column(name = "work_type", nullable = false)
    private String workType;

    @Size(max = 255)
    @NotNull
    @Column(name = "scope_of_work", nullable = false)
    private String scopeOfWork;

    @Column(name = "desired_time", columnDefinition = "interval")
    private Object desiredTime;

}