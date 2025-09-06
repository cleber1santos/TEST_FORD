from moviepy.video.io.VideoFileClip import VideoFileClip

# Caminho do vídeo original
video_path = "d:/TEST-FORD/testeIMG/meu_video.mp4"

# Caminho do vídeo cortado
output_path = "d:/TEST-FORD/testeIMG/meu_video_cortado.mp4"

# Duração do corte em segundos (3 minutos 47 segundos)
tempo_corte = 3*60 + 47  # 227 segundos

# Abrir vídeo
with VideoFileClip(video_path) as video:
    # Criar subclip do início até 3min47s
    video_cortado = video.subclipped(0, tempo_corte)
    # Salvar vídeo cortado
    video_cortado.write_videofile(output_path, codec="libx264")

print("Vídeo cortado salvo em:", output_path)
