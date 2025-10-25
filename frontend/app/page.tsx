export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted">
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          Proje Yöneticisi AI Asistanı
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Yapay zeka destekli proje analizi, görev yönetimi ve kaynak tahsisi
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/contracts/new"
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition"
          >
            Sözleşme Yükle
          </a>
          <a
            href="/projects"
            className="px-6 py-3 border border-input rounded-lg hover:bg-accent transition"
          >
            Projeleri Görüntüle
          </a>
        </div>
      </div>
    </div>
  );
}
