package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.junit.jupiter.api.*;
import static org.example.Utils.getRandDuration;
import static org.example.Utils.getRandString;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Random;

public class WorkPlanDBDaoTest {
    private WorkPlanDao workPlanDBDao;
    private TeamDao teamDBDao;
    private int initialDatabaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        initializeDaoObjects();
        initialDatabaseSize = workPlanDBDao.findAll().size();
    }

    private void initializeDaoObjects() throws Exception {
        var manager = DAOManager.getInstance();
        workPlanDBDao = (WorkPlanDao) manager.getDAO(DAOManager.Table.WORKPLAN);
        teamDBDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
    }

    @Test
    public void testCreate() throws Exception {
        WorkPlan workPlan = createWorkPlan();
        workPlanDBDao.create(workPlan);
        verifyWorkPlanCreation(workPlan);
        initialDatabaseSize++;
    }

    private WorkPlan createWorkPlan() throws Exception {
        WorkPlan workPlan = new WorkPlan();
        workPlan.setDescription(getRandString(10));
        workPlan.setDuration(getRandDuration());
        List<Team> teams = teamDBDao.findAll();
        if (!teams.isEmpty()) {
            Team team = teams.get(new Random().nextInt(teams.size()));
            workPlan.setTeam(team);
        }
        return workPlan;
    }

    private void verifyWorkPlanCreation(WorkPlan workPlan) throws Exception {
        List<WorkPlan> workPlans = workPlanDBDao.findAll();
        assertEquals(initialDatabaseSize + 1, workPlans.size());
        verifyWorkPlanDetails(workPlan, workPlans);
    }

    private void verifyWorkPlanDetails(WorkPlan workPlan, Iterable<WorkPlan> workPlans) {
        for (WorkPlan gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(workPlan.getDescription(), gotWorkPlan.getDescription());
                assertEquals(workPlan.getDuration(), gotWorkPlan.getDuration());
                assertEquals(workPlan.getTeam().getTeamId(), gotWorkPlan.getTeam().getTeamId());
            }
        }
    }

    @Test
    public void testRead() throws Exception {
        WorkPlan workPlan = createWorkPlan();
        workPlanDBDao.create(workPlan);
        verifyWorkPlanCreation(workPlan);

        WorkPlan gotWorkPlan = workPlanDBDao.read(workPlan.getWorkPlanId());
        assertNotNull(gotWorkPlan);
        assertEquals(workPlan.getDescription(), gotWorkPlan.getDescription());
        assertEquals(workPlan.getDuration(), gotWorkPlan.getDuration());
        assertEquals(workPlan.getTeam().getTeamId(), gotWorkPlan.getTeam().getTeamId());
    }

    @Test
    public void testUpdate() throws Exception {
        WorkPlan workPlan = createWorkPlan();
        workPlanDBDao.create(workPlan);
        verifyWorkPlanCreation(workPlan);

        WorkPlan updatedWorkPlan = createWorkPlan();
        updatedWorkPlan.setWorkPlanId(workPlan.getWorkPlanId());
        workPlanDBDao.update(updatedWorkPlan);

        List<WorkPlan> workPlans = workPlanDBDao.findAll();
        assertEquals(initialDatabaseSize + 1, workPlans.size());
        verifyWorkPlanDetails(updatedWorkPlan, workPlans);
    }

    @Test
    public void testDelete() throws Exception {
        WorkPlan workPlan = createWorkPlan();
        workPlanDBDao.create(workPlan);
        verifyWorkPlanCreation(workPlan);

        workPlanDBDao.delete(workPlan.getWorkPlanId());
        List<WorkPlan> workPlans = workPlanDBDao.findAll();
        assertEquals(initialDatabaseSize, workPlans.size());
    }

    @Test
    public void testFindAll() throws Exception {
        List<WorkPlan> workPlans = workPlanDBDao.findAll();
        assertEquals(initialDatabaseSize, workPlans.size());
    }

    @Test
    public void testFindAllByTeam() throws Exception {
        List<Team> teams = teamDBDao.findAll();
        if (!teams.isEmpty()) {
            Team team = teams.get(new Random().nextInt(teams.size()));
            List<WorkPlan> workPlans = workPlanDBDao.findByTeamId(team.getTeamId());
            for (WorkPlan workPlan : workPlans) {
                assertEquals(team.getTeamId(), workPlan.getTeam().getTeamId());
            }
        }
    }

    @Test
    public void testFindAllByDispatcher() throws Exception {
        List<Team> teams = teamDBDao.findAll();
        if (!teams.isEmpty()) {
            Team team = teams.get(new Random().nextInt(teams.size()));
            List<WorkPlan> workPlans = workPlanDBDao.findByDispatcherId(team.getDispatcher().getSpecialistId());
            for (WorkPlan workPlan : workPlans) {
                var team1 = workPlan.getTeam();
                var gotTeam = teamDBDao.read(team1.getTeamId());
                var dispatcher = gotTeam.getDispatcher();
                assertEquals(team.getDispatcher().getSpecialistId(), dispatcher.getSpecialistId());
            }
        }
    }

    @AfterEach
    public void tearDown() throws Exception {
        DAOManager.getInstance().close();
    }
}
