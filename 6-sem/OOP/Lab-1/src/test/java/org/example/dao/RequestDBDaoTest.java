package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Request;
import org.junit.jupiter.api.*;

import java.sql.SQLException;

import static org.example.Utils.getRandDuration;
import static org.example.Utils.getRandString;
import static org.junit.jupiter.api.Assertions.*;

public class RequestDBDaoTest {
    private TenantDao tenantDBDao;
    private RequestDao requestDBDao;
    private int dataBaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        requestDBDao = (RequestDao) manager.getDAO(DAOManager.Table.REQUEST);
        tenantDBDao = (TenantDao) manager.getDAO(DAOManager.Table.TENANT);
        dataBaseSize = requestDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        var request = new Request();
        var tenants = tenantDBDao.findAll();
        var tenantId = tenants.get((int) (Math.random() * tenants.size())).getTenantId();
        var workType = getRandString(10);
        var scopeOfWork = getRandString(10);
        var desiredTime = getRandDuration();
        request.getTenant().setTenantId(tenantId);
        request.setWorkType(workType);
        request.setScopeOfWork(scopeOfWork);
        request.setDesiredTime(desiredTime);

        requestDBDao.create(request);
        var requests = requestDBDao.findAll();

        assertEquals(dataBaseSize + 1, requests.size());
        // get request with the set index
        for (var gotRequest : requests) {
            if (gotRequest.getRequestId() == request.getRequestId()) {
                assertEquals(tenantId, gotRequest.getTenant().getTenantId());
                assertEquals(workType, gotRequest.getWorkType());
                assertEquals(scopeOfWork, gotRequest.getScopeOfWork());
                assertEquals(desiredTime, gotRequest.getDesiredTime());
            }
        }
        dataBaseSize++;
    }

    @Test
    public void testRead() throws Exception {
        var request = new Request();
        var tenants = tenantDBDao.findAll();
        var tenantId = tenants.get((int) (Math.random() * tenants.size())).getTenantId();
        var workType = getRandString(10);
        var scopeOfWork = getRandString(10);
        var desiredTime = getRandDuration();
        request.getTenant().setTenantId(tenantId);
        request.setWorkType(workType);
        request.setScopeOfWork(scopeOfWork);
        request.setDesiredTime(desiredTime);

        requestDBDao.create(request);
        var gotRequest = requestDBDao.read(request.getRequestId());
        assertNotNull(gotRequest);
        assertEquals(request.getRequestId(), gotRequest.getRequestId());
        assertEquals(tenantId, gotRequest.getTenant().getTenantId());
        assertEquals(workType, gotRequest.getWorkType());
        assertEquals(scopeOfWork, gotRequest.getScopeOfWork());
        assertEquals(desiredTime, gotRequest.getDesiredTime());
    }


    @Test
    public void testUpdate() throws Exception {
        var request = new Request();
        var tenants = tenantDBDao.findAll();
        var tenantId = tenants.get((int) (Math.random() * tenants.size())).getTenantId();
        var workType = getRandString(10);
        var scopeOfWork = getRandString(10);
        var desiredTime = getRandDuration();
        request.getTenant().setTenantId(tenantId);
        request.setWorkType(workType);
        request.setScopeOfWork(scopeOfWork);
        request.setDesiredTime(desiredTime);

        requestDBDao.create(request);
        var requests = requestDBDao.findAll();
        assertEquals(dataBaseSize + 1, requests.size());
        for (var gotRequest : requests) {
            if (gotRequest.getRequestId() == request.getRequestId()) {
                assertEquals(tenantId, gotRequest.getTenant().getTenantId());
                assertEquals(workType, gotRequest.getWorkType());
                assertEquals(scopeOfWork, gotRequest.getScopeOfWork());
                assertEquals(desiredTime, gotRequest.getDesiredTime());
            }
        }
    }

    @Test
    public void testDelete() throws Exception {
        var request = new Request();
        var tenants = tenantDBDao.findAll();
        var tenantId = tenants.get((int) (Math.random() * tenants.size())).getTenantId();
        var workType = getRandString(10);
        var scopeOfWork = getRandString(10);
        var desiredTime = getRandDuration();
        request.getTenant().setTenantId(tenantId);
        request.setWorkType(workType);
        request.setScopeOfWork(scopeOfWork);
        request.setDesiredTime(desiredTime);

        requestDBDao.create(request);
        var requests = requestDBDao.findAll();
        assertEquals(dataBaseSize + 1, requests.size());
        for (var gotRequest : requests) {
            if (gotRequest.getRequestId() == request.getRequestId()) {
                assertEquals(tenantId, gotRequest.getTenant().getTenantId());
                assertEquals(workType, gotRequest.getWorkType());
                assertEquals(scopeOfWork, gotRequest.getScopeOfWork());
                assertEquals(desiredTime, gotRequest.getDesiredTime());
            }
        }

        requestDBDao.delete(request.getRequestId());
        requests = requestDBDao.findAll();
        assertEquals(dataBaseSize, requests.size());
        for (var gotRequest : requests) {
            assertNotEquals(request.getRequestId(), gotRequest.getRequestId());
        }
        dataBaseSize--;
    }

    @Test
    public void testFindAll() throws Exception {
        var requests = requestDBDao.findAll();
        assertEquals(dataBaseSize, requests.size());
    }

    @AfterEach
    public void tearDown() throws SQLException {
        var manager = DAOManager.getInstance();
        manager.close();
    }

}
