package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.junit.jupiter.api.*;

import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.*;

public class TeamDBDaoTest {
    private TeamDao teamDBDao;
    private SpecialistDao specialistDBDao;
    private int dataBaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        teamDBDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
        specialistDBDao = (SpecialistDao) manager.getDAO(DAOManager.Table.SPECIALIST);
        dataBaseSize = teamDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        team.setDispatcher(new Specialist());
        team.getDispatcher().setSpecialistId(specialistId);

        teamDBDao.create(team);
        var teams = teamDBDao.findAll();

        assertEquals(dataBaseSize + 1, teams.size());
        // get team with the set index
        for (var gotTeam : teams) {
            if (gotTeam.getTeamId() == team.getTeamId()) {
                assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());
            }
        }
        dataBaseSize++;
    }

    @Test
    public void testRead() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        team.setDispatcher(new Specialist());
        team.getDispatcher().setSpecialistId(specialistId);

        teamDBDao.create(team);
        var gotTeam = teamDBDao.read(team.getTeamId());
        assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());
    }

    @Test
    public void testUpdate() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        team.setDispatcher(new Specialist());
        team.getDispatcher().setSpecialistId(specialistId);

        teamDBDao.create(team);
        var gotTeam = teamDBDao.read(team.getTeamId());
        assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());

        var updatedSpecialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        gotTeam.getDispatcher().setSpecialistId(updatedSpecialistId);
        teamDBDao.update(gotTeam);

        var updatedTeam = teamDBDao.read(gotTeam.getTeamId());
        assertEquals(updatedSpecialistId, updatedTeam.getDispatcher().getSpecialistId());
    }

    @Test
    public void testDelete() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        team.setDispatcher(new Specialist());
        team.getDispatcher().setSpecialistId(specialistId);

        teamDBDao.create(team);
        var teams = teamDBDao.findAll();
        assertEquals(dataBaseSize + 1, teams.size());
        for (var gotTeam : teams) {
            if (gotTeam.getTeamId() == team.getTeamId()) {
                assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());
            }
        }

        teamDBDao.delete(team.getTeamId());
        teams = teamDBDao.findAll();
        assertEquals(dataBaseSize, teams.size());
        for (var gotTeam : teams) {
            assertNotEquals(team.getTeamId(), gotTeam.getTeamId());
        }
    }

    @Test
    public void testFindAll() throws Exception {
        var teams = teamDBDao.findAll();
        for (var team : teams) {
            assertNotNull(team.getTeamId());
            assertNotNull(team.getDispatcher().getSpecialistId());
        }
    }

    @AfterEach
    public void tearDown() throws SQLException {
        var manager = DAOManager.getInstance();
        manager.close();
    }
}
