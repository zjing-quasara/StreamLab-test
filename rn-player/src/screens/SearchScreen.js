import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Image,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { searchVideo } from '../utils/api';

export default function SearchScreen({ route, navigation }) {
  const { keyword } = route.params;
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState([]);

  useEffect(() => {
    doSearch();
  }, []);

  const doSearch = async () => {
    setLoading(true);
    try {
      const data = await searchVideo(keyword);
      setResults(data);
    } catch (error) {
      console.log('搜索失败:', error);
    }
    setLoading(false);
  };

  const selectMovie = (item) => {
    navigation.navigate('Play', { movie: item });
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.resultItem} onPress={() => selectMovie(item)}>
      <Image source={{ uri: item.pic }} style={styles.poster} />
      <View style={styles.info}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.meta}>{item.source} · {item.remarks}</Text>
        <Text style={styles.episodes}>共 {item.episodes.length} 集</Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#00d4ff" />
        <Text style={styles.loadingText}>搜索中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerText}>搜索: {keyword}</Text>
        <Text style={styles.headerText}>找到 {results.length} 个结果</Text>
      </View>

      {results.length > 0 ? (
        <FlatList
          data={results}
          keyExtractor={(item, index) => index.toString()}
          renderItem={renderItem}
        />
      ) : (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>没有找到相关资源</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    padding: 15,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#888',
    marginTop: 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  headerText: {
    color: '#888',
    fontSize: 13,
  },
  resultItem: {
    flexDirection: 'row',
    backgroundColor: '#1a1a2e',
    padding: 12,
    borderRadius: 10,
    marginBottom: 12,
  },
  poster: {
    width: 80,
    height: 110,
    borderRadius: 6,
    backgroundColor: '#333',
  },
  info: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  name: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 6,
  },
  meta: {
    color: '#888',
    fontSize: 12,
    marginBottom: 4,
  },
  episodes: {
    color: '#00d4ff',
    fontSize: 12,
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#666',
    fontSize: 15,
  },
});

