namespace web_api;

public class WeatherForecast
{
    public DateTime Datetime { get; set; }

    public int TemperatureC { get; set; }

    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);

    public string? Conditions { get; set; }

    public string? PostalCode { get; set; }
}
