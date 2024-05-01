package org.example.repository;

import org.example.dao.SpecialistDao;
import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.example.repository.impl.SpecialistRepositoryImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.ArrayList;

import static org.example.Utils.getRandDuration;
import static org.mockito.Mockito.*;

public class SpecialistRepositoryTest {
    @Mock
    private SpecialistDao specialistDao;

    @Mock
    private TeamDao teamDao;

    @Mock
    private WorkPlanDao workPlanDao;

    @InjectMocks
    private SpecialistRepositoryImpl specialistRepository;

    @BeforeEach
    public void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void create() throws Exception {
        var specialist = new Specialist();
        specialist.setWorkPlans(new ArrayList<>());
        specialist.setTeam(null);

        specialistRepository.create(specialist);

        verify(specialistDao, times(1)).create(specialist);
        verify(teamDao, times(0)).read(any());
        verify(teamDao, times(0)).create(any());
        verify(teamDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void createWithTeam() throws Exception {
        var specialist = new Specialist();
        specialist.setWorkPlans(new ArrayList<>());
        specialist.setTeam(new Team());

        when(teamDao.read(any())).thenReturn(new Team());

        when(teamDao.read(any())).thenReturn(null);

        specialistRepository.create(specialist);

        verify(specialistDao, times(1)).create(specialist);
        verify(teamDao, times(1)).read(any());
        verify(teamDao, times(1)).create(any());
        verify(teamDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void createWithWorkPlans() throws Exception {
        var specialist = new Specialist();
        specialist.setWorkPlans(new ArrayList<>());
        specialist.setTeam(null);

        var workPlan = new WorkPlan();
        workPlan.setDuration(getRandDuration());
        specialist.getWorkPlans().add(workPlan);

        specialistRepository.create(specialist);

        verify(specialistDao, times(1)).create(specialist);
        verify(teamDao, times(0)).read(any());
        verify(teamDao, times(0)).create(any());
        verify(teamDao, times(0)).update(any());
        verify(workPlanDao, times(1)).read(any());
        verify(workPlanDao, times(1)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void updateWithTeam() throws Exception {
        var specialist = new Specialist();
        var team = new Team();
        specialist.setWorkPlans(new ArrayList<>());
        specialist.setTeam(team);

        when(teamDao.read(any())).thenReturn(team);

        var newTeam = team;
        newTeam.setDispatcher(new Specialist());
        specialist.setTeam(newTeam);

        specialistRepository.update(specialist);

        verify(specialistDao, times(1)).update(specialist);
        verify(teamDao, times(1)).read(any());
        verify(teamDao, times(0)).create(any());
        verify(teamDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void updateWithWorkPlans() throws Exception {
        var specialist = new Specialist();
        specialist.setWorkPlans(new ArrayList<>());
        specialist.setTeam(null);

        var workPlan = new WorkPlan();
        workPlan.setDuration(getRandDuration());
        specialist.getWorkPlans().add(workPlan);

        when(workPlanDao.read(any())).thenReturn(workPlan);

        specialistRepository.update(specialist);

        verify(specialistDao, times(1)).update(specialist);
        verify(teamDao, times(0)).read(any());
        verify(teamDao, times(0)).create(any());
        verify(teamDao, times(0)).update(any());
        verify(workPlanDao, times(1)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void delete() throws Exception {
        var specialist = new Specialist();
        specialist.setWorkPlans(new ArrayList<>());
        specialist.setTeam(null);

        specialistRepository.delete(specialist.getSpecialistId());

        verify(specialistDao, times(1)).delete(specialist.getSpecialistId());
        verify(teamDao, times(0)).read(any());
        verify(teamDao, times(0)).create(any());
        verify(teamDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }
}
