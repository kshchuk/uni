package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Specialist;
import org.junit.jupiter.api.*;

import static org.example.Utils.getRandString;
import static org.junit.jupiter.api.Assertions.*;

public class SpecialistDBDaoTest {
    private SpecialistDao specialistDBDao;
    private int dataBaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        specialistDBDao = (SpecialistDao) manager.getDAO(DAOManager.Table.SPECIALIST);
        dataBaseSize = specialistDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        var specialist = new Specialist();
        var name = getRandString(10);
        var specialization = getRandString(10);

        specialist.setName(name);
        specialist.setSpecializtion(specialization);

        specialistDBDao.create(specialist);
        var specialists = specialistDBDao.findAll();

        assertEquals(dataBaseSize + 1, specialists.size());
        // get specialist with the set index
        for (var gotSpecialist : specialists) {
            if (gotSpecialist.getSpecialistId() == specialist.getSpecialistId()) {
                assertEquals(name, gotSpecialist.getName());
                assertEquals(specialization, gotSpecialist.getSpecializtion());
            }
        }

        dataBaseSize++;
    }

    @Test
    public void testRead() throws Exception {
        var specialist = new Specialist();
        var name = getRandString(10);
        var specialization = getRandString(10);

        specialist.setName(name);
        specialist.setSpecializtion(specialization);

        specialistDBDao.create(specialist);
        var gotSpecialist = specialistDBDao.read(specialist.getSpecialistId());
        assertEquals(name, gotSpecialist.getName());
        assertEquals(specialization, gotSpecialist.getSpecializtion());
    }

    @Test
    public void testUpdate() throws Exception {
        var specialist = new Specialist();
        var name = getRandString(10);
        var specialization = getRandString(10);

        specialist.setName(name);
        specialist.setSpecializtion(specialization);

        specialistDBDao.create(specialist);
        var specialists = specialistDBDao.findAll();
        assertEquals(dataBaseSize + 1, specialists.size());
        for (var gotSpecialist : specialists) {
            if (gotSpecialist.getSpecialistId() == specialist.getSpecialistId()) {
                assertEquals(name, gotSpecialist.getName());
                assertEquals(specialization, gotSpecialist.getSpecializtion());
            }
        }
        dataBaseSize++;
    }

    @Test
    public void testDelete() throws Exception {
        var specialist = new Specialist();
        var name = getRandString(10);
        var specialization = getRandString(10);

        specialist.setName(name);
        specialist.setSpecializtion(specialization);

        specialistDBDao.create(specialist);
        var specialists = specialistDBDao.findAll();
        assertEquals(dataBaseSize + 1, specialists.size());
        for (var gotSpecialist : specialists) {
            if (gotSpecialist.getSpecialistId() == specialist.getSpecialistId()) {
                assertEquals(name, gotSpecialist.getName());
                assertEquals(specialization, gotSpecialist.getSpecializtion());
            }
        }
        dataBaseSize++;

        specialistDBDao.delete(specialist.getSpecialistId());
        specialists = specialistDBDao.findAll();
        assertEquals(dataBaseSize - 1, specialists.size());
        for (var gotSpecialist : specialists) {
            assertNotEquals(specialist.getSpecialistId(), gotSpecialist.getSpecialistId());
        }
        dataBaseSize--;
    }

    @AfterAll
    public static void tearDown() throws Exception {
        var manager = DAOManager.getInstance();
        manager.close();
    }
}
