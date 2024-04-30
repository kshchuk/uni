package org.example.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.dao.db.DAOManager;
import org.example.dto.GetRequestDTO;
import org.example.entity.Specialist;
import org.example.mapper.SpecialistMapper;
import org.example.repository.SpecialistRepository;
import org.example.repository.db.SpecialistRepositoryImpl;
import org.example.service.SpecialistService;
import org.example.service.SpecialistServiceImpl;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.UUID;
import java.util.logging.Logger;

@WebServlet(name = "specialistServlet", value = "/specialist")
public class SpecialistServlet extends HttpServlet {
    Logger logger = Logger.getLogger(SpecialistServlet.class.getName());
    ObjectMapper objectMapper = new ObjectMapper();
    private SpecialistService specialistService;

    public void init() {
        SpecialistRepository specialistRepository = new SpecialistRepositoryImpl();
        specialistService = new SpecialistServiceImpl(specialistRepository);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        GetRequestDTO getRequestDTO = objectMapper.readValue(body, GetRequestDTO.class);
        Specialist specialist = specialistService.get(UUID.fromString(getRequestDTO.getId()));
        SpecialistMapper.INSTANCE.toDto(specialist);

        String jsonResponse = objectMapper.writeValueAsString(specialist);
        out.write(jsonResponse);
    }

    public void destroy() {
    }
}
