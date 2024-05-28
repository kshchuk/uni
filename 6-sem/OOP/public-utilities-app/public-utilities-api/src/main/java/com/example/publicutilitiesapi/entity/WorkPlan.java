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
@Table(name = "work_plan")
public class WorkPlan {
    @Id
    @Column(name = "work_plan_id", nullable = false)
    private UUID id;

    @Size(max = 255)
    @NotNull
    @Column(name = "description", nullable = false)
    private String description;

    @Column(name = "duration", columnDefinition = "interval")
    private Object duration;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "team_id", nullable = false)
    private Team team;

}