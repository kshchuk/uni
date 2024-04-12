package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.WorkPlan;
import org.junit.jupiter.api.*;

import static org.example.Utils.getRandDuration;
import static org.example.Utils.getRandString;
import static org.junit.jupiter.api.Assertions.*;

public class WorkPlanDBDaoTest {
    private WorkPlanDao workPlanDBDao;
    private TeamDao teamDBDao;
    private int dataBaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        workPlanDBDao = (WorkPlanDao) manager.getDAO(DAOManager.Table.WORKPLAN);
        teamDBDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
        dataBaseSize = workPlanDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        var team = teamDBDao.findAll().get((int) (Math.random() * teamDBDao.findAll().size()));
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlan.setTeam(team);
        workPlanDBDao.create(workPlan);

        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        // get workPlan with the set index
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(description, gotWorkPlan.getDescription());
                assertEquals(duration, gotWorkPlan.getDuration());
                assertEquals(team.getTeamId(), gotWorkPlan.getTeam().getTeamId());
            }
        }
        dataBaseSize++;
    }

    @Test
    public void testRead() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        var team = teamDBDao.findAll().get((int) (Math.random() * teamDBDao.findAll().size()));
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlan.setTeam(team);

        workPlanDBDao.create(workPlan);
        dataBaseSize++;

        var gotWorkPlan = workPlanDBDao.read(workPlan.getWorkPlanId());
        assertEquals(description, gotWorkPlan.getDescription());
        assertEquals(duration, gotWorkPlan.getDuration());
        assertEquals(team.getTeamId(), gotWorkPlan.getTeam().getTeamId());
    }

    @Test
    public void testUpdate() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        var team = teamDBDao.findAll().get((int) (Math.random() * teamDBDao.findAll().size()));
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlan.setTeam(team);

        workPlanDBDao.create(workPlan);

        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(description, gotWorkPlan.getDescription());
                assertEquals(duration, gotWorkPlan.getDuration());
                assertEquals(team.getTeamId(), gotWorkPlan.getTeam().getTeamId());
            }
        }

        var updatedDescription = getRandString(10);
        var updatedDuration = getRandDuration();
        var updatedTeam = teamDBDao.findAll().get((int) (Math.random() * teamDBDao.findAll().size()));
        workPlan.setDescription(updatedDescription);
        workPlan.setDuration(updatedDuration);
        workPlan.setTeam(updatedTeam);
        workPlanDBDao.update(workPlan);

        workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(updatedDescription, gotWorkPlan.getDescription());
                assertEquals(updatedDuration, gotWorkPlan.getDuration());
                assertEquals(updatedTeam.getTeamId(), gotWorkPlan.getTeam().getTeamId());
            }
        }
    }

    @Test
    public void testDelete() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        var team = teamDBDao.findAll().get((int) (Math.random() * teamDBDao.findAll().size()));
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlan.setTeam(team);

        workPlanDBDao.create(workPlan);

        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(description, gotWorkPlan.getDescription());
                assertEquals(duration, gotWorkPlan.getDuration());
                assertEquals(team.getTeamId(), gotWorkPlan.getTeam().getTeamId());
            }
        }

        workPlanDBDao.delete(workPlan.getWorkPlanId());
        workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize, workPlans.size());
    }

    @Test
    public void testFindAll() throws Exception {
        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize, workPlans.size());
    }

    @AfterEach
    public void tearDown() throws Exception {
        var manager = DAOManager.getInstance();
        manager.close();
    }
}
