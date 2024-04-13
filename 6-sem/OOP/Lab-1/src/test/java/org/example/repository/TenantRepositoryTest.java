package org.example.repository;

import org.example.dao.RequestDao;
import org.example.dao.TenantDao;
import org.example.entity.Request;
import org.example.entity.Tenant;
import org.example.repository.db.TenantRepositoryImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.ArrayList;

import static org.example.Utils.getRandDuration;
import static org.mockito.Mockito.*;

public class TenantRepositoryTest {
    @Mock
    private TenantDao tenantDao;

    @Mock
    private RequestDao requestDao;

    @InjectMocks
    private TenantRepositoryImpl tenantRepository;

    @BeforeEach
    public void setup() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void testCreate() throws Exception {
        Tenant tenant = new Tenant();
        Request request = new Request();
        tenant.setRequests(new ArrayList<>(1));
        tenant.getRequests().add(request);

        tenantRepository.create(tenant);

        verify(tenantDao, times(1)).create(tenant);
        verify(requestDao, times(1)).read(request.getId());
        verify(requestDao, times(1)).create(request);
    }

    @Test
    public void testRead() throws Exception {
        Tenant tenant = new Tenant();

        when(tenantDao.read(tenant.getId())).thenReturn(tenant);
        when(requestDao.findByTenantId(tenant.getId())).thenReturn(new ArrayList<>());

        tenant = tenantRepository.read(tenant.getId());
        verify(tenantDao, times(1)).read(tenant.getId());

        tenantRepository.readWithRequests(tenant);
        verify(requestDao, times(1)).findByTenantId(tenant.getId());
    }

    @Test
    public void testUpdateWithNullRequests() throws Exception {
        Tenant tenant = new Tenant();
        tenant.setRequests(null);

        tenantRepository.update(tenant);

        verify(tenantDao, times(1)).update(tenant);
        verify(requestDao, never()).read(any());
        verify(requestDao, never()).update(any());
    }

    @Test
    public void testUpdateWithEmptyRequests() throws Exception {
        Tenant tenant = new Tenant();

        tenantRepository.update(tenant);

        verify(tenantDao, times(1)).update(tenant);
        verify(requestDao, never()).read(any());
        verify(requestDao, never()).update(any());
    }

    @Test
    public void testUpdateWithNewRequests() throws Exception {
        Tenant tenant = new Tenant();
        Request request = new Request();
        tenant.setRequests(new ArrayList<>(1));
        tenant.getRequests().add(request);

        when(requestDao.read(request.getId())).thenReturn(null);

        tenantRepository.update(tenant);

        verify(tenantDao, times(1)).update(tenant);
        verify(requestDao, times(1)).read(request.getId());
        verify(requestDao, times(1)).create(request);
    }

    @Test
    public void testUpdateWithDeletedRequests() throws Exception {
        Tenant tenant = new Tenant();
        tenant.setRequests(new ArrayList<>(1));
        Request request = new Request();
        tenant.getRequests().add(request);

        when(requestDao.read(request.getId())).thenReturn(request);
        when(requestDao.findByTenantId(tenant.getId())).thenReturn(tenant.getRequests());

        tenantRepository.update(tenant);

        verify(tenantDao, times(1)).update(tenant);
        verify(requestDao, times(1)).read(request.getId());
        verify(requestDao, never()).create(request);
        verify(requestDao, times(1)).findByTenantId(tenant.getId());
    }

    @Test
    public void testUpdateWithUpdatedRequests() throws Exception {
        Tenant tenant = new Tenant();
        Request request = new Request();
        tenant.setRequests(new ArrayList<>(1));
        tenant.getRequests().add(request);

        when(requestDao.read(request.getId())).thenReturn(request);

        var updatedRequest = new Request();
        updatedRequest.setId(request.getId());
        updatedRequest.setDesiredTime(getRandDuration());
        tenant.getRequests().remove(0);
        tenant.getRequests().add(updatedRequest);

        tenantRepository.update(tenant);

        verify(tenantDao, times(1)).update(tenant);
        verify(requestDao, times(1)).read(request.getId());
        verify(requestDao, times(1)).update(updatedRequest);
    }

    @Test
    public void testDelete() throws Exception {
        var tenant = new Tenant();

        tenantRepository.delete(tenant.getId());

        verify(tenantDao, times(1)).delete(tenant.getId());
    }

    @Test
    public void testFindAll() throws Exception {
        tenantRepository.findAll();

        verify(tenantDao, times(1)).findAll();
    }
}
