package org.example.service.impl;

import org.example.entity.Specialist;
import org.example.entity.WorkPlan;
import org.example.repository.SpecialistRepository;
import org.example.service.SpecialistService;

import java.util.List;
import java.util.UUID;

public class SpecialistServiceImpl implements SpecialistService {
    private final SpecialistRepository specialistRepository;

    public SpecialistServiceImpl(SpecialistRepository specialistRepository) {
        this.specialistRepository = specialistRepository;
    }

    @Override
    public List<WorkPlan> getWorkPlans(UUID specialistId) {
        var specialist = specialistRepository.read(specialistId);
        specialist = specialistRepository.readWithWorkPlans(specialist);
        return specialist.getWorkPlans();
    }

    @Override
    public void create(Specialist specialist) {
        specialistRepository.create(specialist);
    }

    @Override
    public Specialist get(UUID uuid) {
        Specialist specialist = specialistRepository.read(uuid);
        specialist = specialistRepository.readWithTeam(specialist);
        specialist = specialistRepository.readWithWorkPlans(specialist);
        return specialist;
    }

    @Override
    public void update(Specialist specialist) {
        specialistRepository.update(specialist);
    }

    @Override
    public boolean delete(UUID uuid) {
        // TODO: implement boolean delete(UUID uuid)
        specialistRepository.delete(uuid);
        return true;
    }

    @Override
    public List<Specialist> getAll() {
        List<Specialist> specialists = specialistRepository.findAll();
        for (Specialist specialist : specialists) {
            specialist = specialistRepository.readWithTeam(specialist);
            specialist = specialistRepository.readWithWorkPlans(specialist);
        }
        return specialists;
    }
}
