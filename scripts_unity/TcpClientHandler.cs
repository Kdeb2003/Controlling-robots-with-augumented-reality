using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public class TcpClientHandler
{
    private TcpClient client;
    private StreamReader reader;
    private StreamWriter writer;
    private CancellationTokenSource cts;

    public event Action<string> OnMessage;
    public bool IsConnected => client != null && client.Connected;

    public async Task ConnectAsync(string host, int port)
    {
        if (IsConnected)
            return;

        client = new TcpClient();
        await client.ConnectAsync(host, port);
        NetworkStream stream = client.GetStream();
        reader = new StreamReader(stream, Encoding.UTF8);
        // Use UTF-8 without BOM to avoid JSON parse issues on the server.
        writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true };
        cts = new CancellationTokenSource();
        _ = Task.Run(() => ReceiveLoop(cts.Token));
    }

    public async Task SendLineAsync(string line)
    {
        if (!IsConnected || writer == null)
            return;
        await writer.WriteLineAsync(line);
    }

    public void Close()
    {
        try
        {
            cts?.Cancel();
            reader?.Dispose();
            writer?.Dispose();
            client?.Close();
        }
        finally
        {
            cts = null;
            reader = null;
            writer = null;
            client = null;
        }
    }

    private async Task ReceiveLoop(CancellationToken token)
    {
        try
        {
            while (!token.IsCancellationRequested && reader != null)
            {
                string line = await reader.ReadLineAsync();
                if (line == null)
                    break;
                OnMessage?.Invoke(line);
            }
        }
        catch
        {
            // Connection issues are handled by caller via reconnect logic.
        }
    }
}
