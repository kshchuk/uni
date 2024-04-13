package org.example.repository;

import org.example.dao.RequestDao;
import org.example.entity.Request;
import org.example.repository.db.RequestRepositoryImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.ArrayList;

import static org.mockito.Mockito.*;

public class RequestRepositoryTest {
    @Mock
    private RequestDao requestDao;

    @InjectMocks
    private RequestRepositoryImpl requestRepository;

    @BeforeEach
    public void setup() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void testCreate() throws Exception {
        Request request = new Request();
        requestRepository.create(request);

        verify(requestDao, times(1)).create(request);
    }

    @Test
    public void testRead() throws Exception {
        Request request = new Request();

        when(requestDao.read(request.getId())).thenReturn(request);

        requestRepository.read(request.getId());

        verify(requestDao, times(1)).read(request.getId());
    }

    @Test
    public void testUpdate() throws Exception {
        Request request = new Request();
        requestRepository.update(request);

        verify(requestDao, times(1)).update(request);
    }

    @Test
    public void testDelete() throws Exception {
        Request request = new Request();

        when(requestDao.read(request.getId())).thenReturn(request);

        requestRepository.delete(request.getId());

        verify(requestDao, times(1)).delete(request.getRequestId());
    }

    @Test
    public void testGetAll() throws Exception {
        ArrayList<Request> requests = new ArrayList<>();
        requests.add(new Request());

        when(requestDao.findAll()).thenReturn(requests);

        requestRepository.findAll();

        verify(requestDao, times(1)).findAll();
    }
}
