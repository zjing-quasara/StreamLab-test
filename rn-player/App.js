import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import HomeScreen from './src/screens/HomeScreen';
import SearchScreen from './src/screens/SearchScreen';
import PlayScreen from './src/screens/PlayScreen';

const Stack = createNativeStackNavigator();

const screenOptions = {
  headerStyle: {
    backgroundColor: '#1a1a2e',
  },
  headerTintColor: '#fff',
  headerTitleStyle: {
    fontWeight: 'bold',
  },
  contentStyle: {
    backgroundColor: '#0a0a0f',
  },
};

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={screenOptions}>
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'StreamLab' }}
        />
        <Stack.Screen
          name="Search"
          component={SearchScreen}
          options={{ title: '搜索结果' }}
        />
        <Stack.Screen
          name="Play"
          component={PlayScreen}
          options={{ title: '播放', headerShown: false }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

