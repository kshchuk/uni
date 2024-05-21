package com.example.publicutilitiesapi.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.UUID;

@Getter
@Setter
@Entity
@Table(name = "team")
public class Team {
    @Id
    @Column(name = "team_id", nullable = false)
    private UUID id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "dispatcher_id", nullable = false)
    private Specialist dispatcher;

    @OneToMany(mappedBy = "team")
    private Set<Specialist> specialists = new LinkedHashSet<>();

    @OneToMany(mappedBy = "team")
    private Set<WorkPlan> workPlans = new LinkedHashSet<>();

}