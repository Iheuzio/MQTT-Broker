using Microsoft.AspNetCore.Mvc;

namespace web_api.Controllers;

[ApiController]
[Route("weather-forecast")]
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

    private readonly List<string> _postalCodes = new List<string> { "M9A 1A8", "M5S 1A1", "M4W 1A5", "M6G 1A1", "M5R 1A6" };

    private readonly ILogger<WeatherForecastController> _logger;

    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
        _logger = logger;
    }

    [HttpGet("postal-code/{postalCode}", Name = "weather-forecast")]
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
        var conditions = _conditions[Random.Shared.Next(_conditions.Length)];
        string intensity;
        // for conditions with intensity, generate it
        if (conditions == "Snowfall" || conditions == "Rain")
        {
            intensity = _intensities[Random.Shared.Next(_conditions.Length - 1)];
        }
        // for other conditions, set to n/a (last element in array)
        else intensity = _intensities[_conditions.Length - 1];
        return new WeatherForecast
        {
            Datetime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
            TemperatureC = Random.Shared.Next(-40, 40),
            Conditions = conditions,
            Intensity = intensity,
            //return postal code from the request
            PostalCode = postalCode
        };
    }
}
