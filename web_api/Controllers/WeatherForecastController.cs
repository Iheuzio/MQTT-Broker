using Microsoft.AspNetCore.Mvc;

namespace web_api.Controllers;

[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] Conditions = new[]
    {
        "Snowfall", "Rain", "Sunny", "Cloudy"
    };
    private static readonly string[] Intensities = new[]
    {
        "heavy", "medium", "light", "n/a"
    };

    private readonly ILogger<WeatherForecastController> _logger;

    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
        _logger = logger;
    }

    [HttpGet(Name = "GetWeatherForecast")]
    [ProducesResponseType(typeof(IEnumerable<WeatherForecast>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
    [Produces("application/json")]
    public ActionResult<Object> Get()
    {
        //return BadRequest("Error message for Bad Request (to be managed in a try/catch block)");
        return new WeatherForecast(
        {
            Datetime = DateOnly.FromDateTime(DateTime.Now),
            TemperatureC = Random.Shared.Next(-40, 40),
            Conditions = Conditions[Random.Shared.Next(Conditions.Length)],
            PostalCode = //return postal code from the request
        });
    }
}
