using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;

namespace web_api.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class MotionDetectionController : ControllerBase
    {
        private readonly ILogger<MotionDetectionController> _logger;
        private readonly List<string> _postalCodes = new List<string> { "M9A 1A8", "M5S 1A1", "M4W 1A5", "M6G 1A1", "M5R 1A6" };

        public MotionDetectionController(ILogger<MotionDetectionController> logger)
        {
            _logger = logger;
        }

        [HttpGet(Name = "MotionDetectionController")]
        [ProducesResponseType(typeof(IEnumerable<MotionDetectionController>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [Produces("application/json")]
        public ActionResult<Object> Get(string postal_code)
        {
            if (!_postalCodes.Contains(postal_code))
            {
                return BadRequest("Invalid postal code");
            }

            var random = new Random();
            var detectionType = random.Next(2) == 0 ? "motion" : "collision";
            var detectionValue = random.Next(2) == 0 ? true : false;
            var dateTime = DateTime.Now.ToString("yyyy-MM-dd-HH:mm:ss");

            var result = new
            {
                postal_code = postal_code,
                detection = new { type = detectionType, value = detectionValue },
                datetime = dateTime
            };

            // Extract JWT token from request headers
            var jwtToken = Request.Headers["Authorization"].ToString().Replace("Bearer ", "");
            if (!ValidateJwtToken(jwtToken))
            {
                return Unauthorized("Invalid JWT token");
            }

            // Your logic for processing the result
            // ...

            return Ok(result);
        }

        private bool ValidateJwtToken(string token)
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.ASCII.GetBytes("secretkey");

            try
            {
                tokenHandler.ValidateToken(token, new TokenValidationParameters
                {
                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = new SymmetricSecurityKey(key),
                    ValidateIssuer = false,
                    ValidateAudience = false,
                    ClockSkew = TimeSpan.Zero
                }, out _);
                return true;
            }
            catch
            {
                return false;
            }
        }
    }
}
