using Microsoft.AspNetCore.Mvc;

namespace web_api.Controllers;

[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] _conditions = new[]
    {
        "Snowfall", "Rain", "Sunny", "Cloudy"
    };
    private static readonly string[] _intensities = new[]
    {
        "heavy", "medium", "light", "n/a"
    };

    private readonly List<string> _postalCodes = new List<string> { "M9A1A8", "M5S1A1", "M4W1A5", "M6G1A1", "M5R1A6" };

    private readonly ILogger<WeatherForecastController> _logger;

    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
        _logger = logger;
    }

    [HttpGet("postal-code/{postalCode}", Name = "GetWeatherForecast")]
    [ProducesResponseType(typeof(IEnumerable<WeatherForecast>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
    [Produces("application/json")]
    public ActionResult<Object> Get(string postalCode)
    {
        if (!_postalCodes.Contains(postalCode))
        {
            return NotFound("Unknown Postal Code");
        }
        return new WeatherForecast
        {
            Datetime = DateTime.Now,
            TemperatureC = Random.Shared.Next(-40, 40),
            Conditions = _conditions[Random.Shared.Next(_conditions.Length)],
            //return postal code from the request
            PostalCode = postalCode
        };
    }
}
