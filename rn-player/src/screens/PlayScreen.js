import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Dimensions,
} from 'react-native';
import Video from 'react-native-video';

const { width } = Dimensions.get('window');

export default function PlayScreen({ route }) {
  const { movie } = route.params;
  const [currentIndex, setCurrentIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const [loading, setLoading] = useState(true);
  const videoRef = useRef(null);

  const currentEpisode = movie.episodes[currentIndex];

  const playEpisode = (index) => {
    setCurrentIndex(index);
    setLoading(true);
  };

  const onLoad = () => {
    setLoading(false);
  };

  const onError = (error) => {
    console.log('视频加载失败:', error);
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      {/* 视频播放器 */}
      <View style={styles.videoContainer}>
        <Video
          ref={videoRef}
          source={{ uri: currentEpisode.url }}
          style={styles.video}
          controls={true}
          resizeMode="contain"
          paused={paused}
          onLoad={onLoad}
          onError={onError}
        />
        {loading && (
          <View style={styles.loadingOverlay}>
            <Text style={styles.loadingText}>加载中...</Text>
          </View>
        )}
      </View>

      {/* 视频信息 */}
      <View style={styles.info}>
        <Text style={styles.title}>{movie.name}</Text>
        <Text style={styles.episode}>正在播放: {currentEpisode.name}</Text>
      </View>

      {/* 剧集选择 */}
      <View style={styles.episodesSection}>
        <Text style={styles.sectionTitle}>
          选集 (共{movie.episodes.length}集)
        </Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.episodesList}>
            {movie.episodes.map((ep, index) => (
              <TouchableOpacity
                key={index}
                style={[
                  styles.epBtn,
                  index === currentIndex && styles.epBtnActive,
                ]}
                onPress={() => playEpisode(index)}
              >
                <Text
                  style={[
                    styles.epBtnText,
                    index === currentIndex && styles.epBtnTextActive,
                  ]}
                >
                  {index + 1}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  videoContainer: {
    width: width,
    height: width * 0.5625, // 16:9
    backgroundColor: '#000',
  },
  video: {
    width: '100%',
    height: '100%',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  loadingText: {
    color: '#fff',
    fontSize: 14,
  },
  info: {
    padding: 15,
  },
  title: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  episode: {
    color: '#888',
    fontSize: 13,
  },
  episodesSection: {
    padding: 15,
  },
  sectionTitle: {
    color: '#888',
    fontSize: 14,
    marginBottom: 12,
  },
  episodesList: {
    flexDirection: 'row',
    gap: 10,
  },
  epBtn: {
    width: 45,
    height: 45,
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  epBtnActive: {
    backgroundColor: '#00d4ff',
  },
  epBtnText: {
    color: '#fff',
    fontSize: 14,
  },
  epBtnTextActive: {
    color: '#000',
    fontWeight: 'bold',
  },
});

