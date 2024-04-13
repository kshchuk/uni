package org.example.repository;

import org.example.dao.*;
import org.example.entity.*;
import org.example.repository.db.SpecialistRepositoryImpl;
import org.example.repository.db.TeamRepositoryImpl;
import org.example.repository.db.TenantRepositoryImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.ArrayList;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class TeamRepositoryTest {
    @Mock
    private TeamDao teamDao;

    @Mock
    private SpecialistDao specialistDao;

    @Mock
    private WorkPlanDao workPlanDao;

    @InjectMocks
    private TeamRepositoryImpl teamRepository;

    @BeforeEach
    public void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void create() throws Exception {
        var team = new Team();
        team.setWorkPlans(new ArrayList<>());
        team.setSpecialists(new ArrayList<>());
        team.setDispatcher(null);

        teamRepository.create(team);

        verify(teamDao, times(1)).create(team);
        verify(specialistDao, times(0)).read(any());
        verify(specialistDao, times(0)).create(any());
        verify(specialistDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void createWithSpecialists() throws Exception {
        var team = new Team();
        team.setWorkPlans(new ArrayList<>());
        var specialist = new Specialist();
        team.setSpecialists(new ArrayList<>(1));
        team.getSpecialists().add(specialist);
        team.setDispatcher(new Specialist());

        when(specialistDao.read(any())).thenReturn(specialist);

        teamRepository.create(team);

        verify(teamDao, times(1)).create(team);
        verify(specialistDao, times(1)).read(any());
        verify(specialistDao, times(0)).create(any());
        verify(specialistDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void createWithSpecialistsAndWorkPlans() throws Exception {
        var team = new Team();
        var specialist = new Specialist();
        var workPlan = new WorkPlan();
        team.setWorkPlans(new ArrayList<>(1));
        team.setSpecialists(new ArrayList<>(1));
        team.getWorkPlans().add(workPlan);
        team.getSpecialists().add(specialist);
        team.setDispatcher(new Specialist());

        when(specialistDao.read(any())).thenReturn(null);
        when(workPlanDao.read(any())).thenReturn(null);

        teamRepository.create(team);

        verify(teamDao, times(1)).create(team);
        verify(specialistDao, times(1)).read(any());
        verify(specialistDao, times(1)).create(any());
        verify(specialistDao, times(0)).update(any());
        verify(workPlanDao, times(1)).read(any());
        verify(workPlanDao, times(1)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void update() throws Exception {
        var team = new Team();
        team.setWorkPlans(new ArrayList<>());
        team.setSpecialists(new ArrayList<>());
        team.setDispatcher(null);

        teamRepository.update(team);

        verify(teamDao, times(1)).update(team);
        verify(specialistDao, times(0)).read(any());
        verify(specialistDao, times(0)).create(any());
        verify(specialistDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }

    @Test
    public void updateWithSpecialistsAndWorkPlans() throws Exception {
        var team = new Team();
        var specialist = new Specialist();
        var workPlan = new WorkPlan();
        team.setWorkPlans(new ArrayList<>(1));
        team.getWorkPlans().add(workPlan);
        team.setSpecialists(new ArrayList<>(1));
        team.getSpecialists().add(specialist);
        team.setDispatcher(new Specialist());

        when(specialistDao.read(any())).thenReturn(new Specialist());
        when(workPlanDao.read(any())).thenReturn(new WorkPlan());

        teamRepository.update(team);

        verify(teamDao, times(1)).update(team);
        verify(specialistDao, times(1)).read(any());
        verify(specialistDao, times(0)).create(any());
        verify(specialistDao, times(1)).update(any());
        verify(workPlanDao, times(1)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(1)).update(any());
    }

    @Test
    public void delete() throws Exception {
        var team = new Team();
        team.setWorkPlans(new ArrayList<>());
        team.setSpecialists(new ArrayList<>());
        team.setDispatcher(null);

        teamRepository.delete(team.getTeamId());

        verify(teamDao, times(1)).delete(team.getTeamId());
        verify(specialistDao, times(0)).read(any());
        verify(specialistDao, times(0)).create(any());
        verify(specialistDao, times(0)).update(any());
        verify(workPlanDao, times(0)).read(any());
        verify(workPlanDao, times(0)).create(any());
        verify(workPlanDao, times(0)).update(any());
    }
}
