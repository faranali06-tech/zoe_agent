import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:webview_flutter/webview_flutter.dart';

const vapiPublicKey = 'ace23776-0d1f-4038-9cd9-c7a088f0b0a4';
const zoeAssistantId = 'b849fdf5-e367-49dc-ae33-c863788c7819';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ZoeApp());
}

class ZoeApp extends StatelessWidget {
  const ZoeApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Zoe Agent',
      theme: ThemeData.dark(),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _inCall = false;

  Future<void> _checkPermissions() async {
    await Permission.microphone.request();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Zoe Control Room')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                _inCall ? 'Zoe is Active Server Connection Live' : 'Zoe is Standby Mode',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  backgroundColor: Colors.green,
                ),
                icon: const Icon(Icons.phone),
                label: const Text('Test Vapi Call (No Wake Word)', style: TextStyle(fontSize: 16)),
                onPressed: () async {
                  await _checkPermissions();
                  setState(() => _inCall = true);
                  if (!mounted) return;
                  await Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const VapiCallWebView()),
                  );
                  setState(() => _inCall = false);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class VapiCallWebView extends StatefulWidget {
  const VapiCallWebView({super.key});
  @override
  State<VapiCallWebView> createState() => _VapiCallWebViewState();
}

class _VapiCallWebViewState extends State<VapiCallWebView> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadHtmlString('''
<!doctype html>
<html>
  <head><meta name="viewport" content="width=device-width, initial-scale=1.0"/></head>
  <body style="background-color: #121212; color: white; text-align: center; font-family: sans-serif; padding-top: 50px;">
    <h2>Connecting to Zoe...</h2>
    <p>Please speak now, Boss.</p>
    <script type="module">
      import Vapi from "https://jsdelivr.net";
      const vapi = new Vapi("${vapiPublicKey}");
      vapi.start("${zoeAssistantId}");
      window.vapi = vapi;
    </script>
  </body>
</html>
''');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Zoe Live Audio'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: WebViewWidget(controller: _controller),
    );
  }
}
